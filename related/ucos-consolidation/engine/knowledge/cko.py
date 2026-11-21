"""UKDA Part 02/03 — Canonical Knowledge Object + Universal Decision Model.

The two authoritative value types of the architecture:

    * :class:`CanonicalKnowledgeObject` (CKO) — Part 02. A single, self-describing,
      immutable unit of institutional knowledge. It carries its own identity,
      classification, authority, ownership, lifecycle, version, traceability, and
      the full link topology (parents/children/dependencies/consumers/knowledge/
      decision/documentation links). A CKO is **content-addressed**: its
      ``content_sha256`` is the canonical hash of every field but the hash itself,
      so any post-authoring mutation is detectable (integrity), duplicates are
      detectable by hash equality (the Knowledge Once Principle), and versions are
      distinguishable.

    * :class:`DecisionRecord` — Part 03. The permanent, never-rediscovered record
      of an architectural decision: problem, context, objective, alternatives,
      evaluation criteria, tradeoffs, rejected options **with reasons**, the chosen
      architecture, rationale, consequences, risks, mitigations, dependencies,
      impact analysis, implementation guidance, validation strategy, certification
      requirements, review authority, and supersession rules. Also content-addressed.

Both types are frozen, slotted, deterministic, and serialisable. They hold no
wall-clock: any ``created``/``updated`` timestamps are author-supplied strings so
serialization — and therefore the content hash — is reproducible (IMP-007 §5).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from engine.knowledge.errors import (
    KnowledgeIntegrityError,
    KnowledgeValidationError,
    LifecycleTransitionError,
)
from engine.knowledge.model import (
    KnowledgeAuthority,
    KnowledgeKind,
    Lifecycle,
    content_hash,
)

# ---------------------------------------------------------------------------
# defensive parsing helpers (mirrors engine.registry.models discipline)
# ---------------------------------------------------------------------------


def _require(record: Mapping[str, Any], key: str, *, at: str) -> Any:
    if key not in record or record[key] is None:
        raise KnowledgeValidationError("required field missing", field=key, at=at)
    return record[key]


def _as_str(value: Any, *, field_name: str, at: str) -> str:
    if not isinstance(value, str) or not value:
        raise KnowledgeValidationError("expected a non-empty string", field=field_name, at=at)
    return value


def _as_opt_str(value: Any, *, field_name: str, at: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise KnowledgeValidationError("expected a string or null", field=field_name, at=at)
    return value


def _as_str_list(value: Any, *, field_name: str, at: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise KnowledgeValidationError("expected an array of strings", field=field_name, at=at)
    return tuple(value)


@dataclass(frozen=True, slots=True)
class RejectedOption:
    """A single rejected alternative and the permanent reason it was rejected."""

    option: str
    reason: str

    @classmethod
    def from_dict(cls, raw: Any, *, at: str) -> RejectedOption:
        if not isinstance(raw, Mapping):
            raise KnowledgeValidationError("rejected option must be an object", at=at)
        return cls(
            option=_as_str(_require(raw, "option", at=at), field_name="option", at=at),
            reason=_as_str(_require(raw, "reason", at=at), field_name="reason", at=at),
        )

    def to_dict(self) -> dict[str, Any]:
        return {"option": self.option, "reason": self.reason}


@dataclass(frozen=True, slots=True)
class CanonicalKnowledgeObject:
    """Part 02 — a single, self-describing, content-addressed unit of knowledge."""

    cko_id: str
    kind: KnowledgeKind
    title: str
    statement: str
    universe: str
    authority: KnowledgeAuthority
    owner: str
    lifecycle: Lifecycle
    version: str
    rationale: str = ""
    parent: str | None = None
    children: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    consumers: tuple[str, ...] = ()
    supersedes: tuple[str, ...] = ()
    superseded_by: str | None = None
    conflicts_with: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    knowledge_links: tuple[str, ...] = ()
    decision_links: tuple[str, ...] = ()
    documentation_links: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    certification: str | None = None
    validation: str | None = None
    created: str | None = None
    updated: str | None = None
    content_sha256: str = ""

    # -- construction ----------------------------------------------------------

    @classmethod
    def create(cls, **fields: Any) -> CanonicalKnowledgeObject:
        """Build a CKO and seal it with a freshly computed content hash."""
        fields.pop("content_sha256", None)
        provisional = cls(**fields)
        return provisional.sealed()

    def sealed(self) -> CanonicalKnowledgeObject:
        """Return a copy whose ``content_sha256`` matches the current field values."""
        from dataclasses import replace

        return replace(self, content_sha256=self._recompute())

    @classmethod
    def from_dict(cls, record: Mapping[str, Any]) -> CanonicalKnowledgeObject:
        if not isinstance(record, Mapping):
            raise KnowledgeValidationError("CKO record must be an object")
        cko_id = _as_str(_require(record, "cko_id", at="cko"), field_name="cko_id", at="cko")
        obj = cls(
            cko_id=cko_id,
            kind=KnowledgeKind.coerce(_require(record, "kind", at=cko_id), context=cko_id),
            title=_as_str(_require(record, "title", at=cko_id), field_name="title", at=cko_id),
            statement=_as_str(
                _require(record, "statement", at=cko_id), field_name="statement", at=cko_id
            ),
            universe=_as_str(
                _require(record, "universe", at=cko_id), field_name="universe", at=cko_id
            ),
            authority=KnowledgeAuthority.coerce(
                _require(record, "authority", at=cko_id), context=cko_id
            ),
            owner=_as_str(_require(record, "owner", at=cko_id), field_name="owner", at=cko_id),
            lifecycle=Lifecycle.coerce(_require(record, "lifecycle", at=cko_id), context=cko_id),
            version=_as_str(
                _require(record, "version", at=cko_id), field_name="version", at=cko_id
            ),
            rationale=record.get("rationale") or "",
            parent=_as_opt_str(record.get("parent"), field_name="parent", at=cko_id),
            children=_as_str_list(record.get("children"), field_name="children", at=cko_id),
            dependencies=_as_str_list(
                record.get("dependencies"), field_name="dependencies", at=cko_id
            ),
            consumers=_as_str_list(record.get("consumers"), field_name="consumers", at=cko_id),
            supersedes=_as_str_list(record.get("supersedes"), field_name="supersedes", at=cko_id),
            superseded_by=_as_opt_str(
                record.get("superseded_by"), field_name="superseded_by", at=cko_id
            ),
            conflicts_with=_as_str_list(
                record.get("conflicts_with"), field_name="conflicts_with", at=cko_id
            ),
            tags=_as_str_list(record.get("tags"), field_name="tags", at=cko_id),
            knowledge_links=_as_str_list(
                record.get("knowledge_links"), field_name="knowledge_links", at=cko_id
            ),
            decision_links=_as_str_list(
                record.get("decision_links"), field_name="decision_links", at=cko_id
            ),
            documentation_links=_as_str_list(
                record.get("documentation_links"), field_name="documentation_links", at=cko_id
            ),
            evidence=_as_str_list(record.get("evidence"), field_name="evidence", at=cko_id),
            certification=_as_opt_str(
                record.get("certification"), field_name="certification", at=cko_id
            ),
            validation=_as_opt_str(record.get("validation"), field_name="validation", at=cko_id),
            created=_as_opt_str(record.get("created"), field_name="created", at=cko_id),
            updated=_as_opt_str(record.get("updated"), field_name="updated", at=cko_id),
            content_sha256=record.get("content_sha256") or "",
        )
        # A stored record with a hash must verify; a record without one is sealed.
        if obj.content_sha256:
            obj.require_integrity()
            return obj
        return obj.sealed()

    # -- integrity -------------------------------------------------------------

    def _core(self) -> dict[str, Any]:
        """The canonical, hashable core (every field except the hash itself)."""
        return {
            "cko_id": self.cko_id,
            "kind": self.kind.value,
            "title": self.title,
            "statement": self.statement,
            "universe": self.universe,
            "authority": self.authority.value,
            "owner": self.owner,
            "lifecycle": self.lifecycle.value,
            "version": self.version,
            "rationale": self.rationale,
            "parent": self.parent,
            "children": list(self.children),
            "dependencies": list(self.dependencies),
            "consumers": list(self.consumers),
            "supersedes": list(self.supersedes),
            "superseded_by": self.superseded_by,
            "conflicts_with": list(self.conflicts_with),
            "tags": list(self.tags),
            "knowledge_links": list(self.knowledge_links),
            "decision_links": list(self.decision_links),
            "documentation_links": list(self.documentation_links),
            "evidence": list(self.evidence),
            "certification": self.certification,
            "validation": self.validation,
            "created": self.created,
            "updated": self.updated,
        }

    def _recompute(self) -> str:
        return content_hash(self._core())

    def semantic_hash(self) -> str:
        """Hash of the knowledge *substance* only (identity/version/links excluded).

        Two objects with an identical semantic hash express the same knowledge under
        different identities — the signature of a Knowledge Once Principle violation.
        Distinct from :attr:`content_sha256`, which also binds identity and topology
        for integrity.
        """
        return content_hash(
            {
                "kind": self.kind.value,
                "statement": self.statement.strip().lower(),
                "rationale": self.rationale.strip().lower(),
            }
        )

    def verify_integrity(self) -> bool:
        """Return True iff the stored content hash matches a recomputation."""
        return bool(self.content_sha256) and self._recompute() == self.content_sha256

    def require_integrity(self) -> None:
        """Raise :class:`KnowledgeIntegrityError` if the object was mutated."""
        if not self.verify_integrity():
            raise KnowledgeIntegrityError(
                "canonical knowledge object integrity check failed",
                cko_id=self.cko_id,
                expected=self.content_sha256,
                actual=self._recompute(),
            )

    # -- lifecycle -------------------------------------------------------------

    @property
    def is_active(self) -> bool:
        """True iff this object is a live source of authority (ratified..operational)."""
        return self.lifecycle.is_active

    def transition_to(
        self, target: Lifecycle, *, updated: str | None = None
    ) -> CanonicalKnowledgeObject:
        """Return a resealed copy advanced to ``target`` (Part 12 transition graph)."""
        self.lifecycle.require_transition(target, at=self.cko_id)
        from dataclasses import replace

        moved = replace(
            self,
            lifecycle=target,
            updated=updated if updated is not None else self.updated,
            content_sha256="",
        )
        return moved.sealed()

    # -- link topology ---------------------------------------------------------

    def all_links(self) -> tuple[str, ...]:
        """Every outbound knowledge/dependency/parent link, de-duplicated & ordered."""
        seen: dict[str, None] = {}
        if self.parent:
            seen.setdefault(self.parent, None)
        for group in (
            self.children,
            self.dependencies,
            self.consumers,
            self.supersedes,
            self.knowledge_links,
        ):
            for ref in group:
                seen.setdefault(ref, None)
        if self.superseded_by:
            seen.setdefault(self.superseded_by, None)
        return tuple(seen)

    def to_dict(self) -> dict[str, Any]:
        payload = self._core()
        payload["content_sha256"] = self.content_sha256
        return payload


@dataclass(frozen=True, slots=True)
class DecisionRecord:
    """Part 03 — the permanent, never-rediscovered record of a decision."""

    decision_id: str
    title: str
    problem_statement: str
    context: str
    objective: str
    chosen_architecture: str
    rationale: str
    authority: KnowledgeAuthority
    owner: str
    lifecycle: Lifecycle
    version: str
    review_authority: str
    supersession_rules: str
    alternatives: tuple[str, ...] = ()
    evaluation_criteria: tuple[str, ...] = ()
    tradeoffs: tuple[str, ...] = ()
    rejected_options: tuple[RejectedOption, ...] = ()
    consequences: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    mitigations: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    impact_analysis: str = ""
    implementation_guidance: str = ""
    validation_strategy: str = ""
    certification_requirements: tuple[str, ...] = ()
    supersedes: str | None = None
    superseded_by: str | None = None
    created: str | None = None
    updated: str | None = None
    content_sha256: str = ""

    @classmethod
    def create(cls, **fields: Any) -> DecisionRecord:
        fields.pop("content_sha256", None)
        return cls(**fields).sealed()

    def sealed(self) -> DecisionRecord:
        from dataclasses import replace

        return replace(self, content_sha256=self._recompute())

    @classmethod
    def from_dict(cls, record: Mapping[str, Any]) -> DecisionRecord:
        if not isinstance(record, Mapping):
            raise KnowledgeValidationError("decision record must be an object")
        did = _as_str(
            _require(record, "decision_id", at="decision"),
            field_name="decision_id",
            at="decision",
        )
        rejected_raw = record.get("rejected_options") or []
        if not isinstance(rejected_raw, list):
            raise KnowledgeValidationError("rejected_options must be an array", at=did)
        obj = cls(
            decision_id=did,
            title=_as_str(_require(record, "title", at=did), field_name="title", at=did),
            problem_statement=_as_str(
                _require(record, "problem_statement", at=did),
                field_name="problem_statement",
                at=did,
            ),
            context=_as_str(_require(record, "context", at=did), field_name="context", at=did),
            objective=_as_str(
                _require(record, "objective", at=did), field_name="objective", at=did
            ),
            chosen_architecture=_as_str(
                _require(record, "chosen_architecture", at=did),
                field_name="chosen_architecture",
                at=did,
            ),
            rationale=_as_str(
                _require(record, "rationale", at=did), field_name="rationale", at=did
            ),
            authority=KnowledgeAuthority.coerce(_require(record, "authority", at=did), context=did),
            owner=_as_str(_require(record, "owner", at=did), field_name="owner", at=did),
            lifecycle=Lifecycle.coerce(_require(record, "lifecycle", at=did), context=did),
            version=_as_str(_require(record, "version", at=did), field_name="version", at=did),
            review_authority=_as_str(
                _require(record, "review_authority", at=did),
                field_name="review_authority",
                at=did,
            ),
            supersession_rules=_as_str(
                _require(record, "supersession_rules", at=did),
                field_name="supersession_rules",
                at=did,
            ),
            alternatives=_as_str_list(
                record.get("alternatives"), field_name="alternatives", at=did
            ),
            evaluation_criteria=_as_str_list(
                record.get("evaluation_criteria"), field_name="evaluation_criteria", at=did
            ),
            tradeoffs=_as_str_list(record.get("tradeoffs"), field_name="tradeoffs", at=did),
            rejected_options=tuple(RejectedOption.from_dict(item, at=did) for item in rejected_raw),
            consequences=_as_str_list(
                record.get("consequences"), field_name="consequences", at=did
            ),
            risks=_as_str_list(record.get("risks"), field_name="risks", at=did),
            mitigations=_as_str_list(record.get("mitigations"), field_name="mitigations", at=did),
            dependencies=_as_str_list(
                record.get("dependencies"), field_name="dependencies", at=did
            ),
            impact_analysis=record.get("impact_analysis") or "",
            implementation_guidance=record.get("implementation_guidance") or "",
            validation_strategy=record.get("validation_strategy") or "",
            certification_requirements=_as_str_list(
                record.get("certification_requirements"),
                field_name="certification_requirements",
                at=did,
            ),
            supersedes=_as_opt_str(record.get("supersedes"), field_name="supersedes", at=did),
            superseded_by=_as_opt_str(
                record.get("superseded_by"), field_name="superseded_by", at=did
            ),
            created=_as_opt_str(record.get("created"), field_name="created", at=did),
            updated=_as_opt_str(record.get("updated"), field_name="updated", at=did),
            content_sha256=record.get("content_sha256") or "",
        )
        if obj.content_sha256:
            obj.require_integrity()
            return obj
        return obj.sealed()

    def _core(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "title": self.title,
            "problem_statement": self.problem_statement,
            "context": self.context,
            "objective": self.objective,
            "chosen_architecture": self.chosen_architecture,
            "rationale": self.rationale,
            "authority": self.authority.value,
            "owner": self.owner,
            "lifecycle": self.lifecycle.value,
            "version": self.version,
            "review_authority": self.review_authority,
            "supersession_rules": self.supersession_rules,
            "alternatives": list(self.alternatives),
            "evaluation_criteria": list(self.evaluation_criteria),
            "tradeoffs": list(self.tradeoffs),
            "rejected_options": [r.to_dict() for r in self.rejected_options],
            "consequences": list(self.consequences),
            "risks": list(self.risks),
            "mitigations": list(self.mitigations),
            "dependencies": list(self.dependencies),
            "impact_analysis": self.impact_analysis,
            "implementation_guidance": self.implementation_guidance,
            "validation_strategy": self.validation_strategy,
            "certification_requirements": list(self.certification_requirements),
            "supersedes": self.supersedes,
            "superseded_by": self.superseded_by,
            "created": self.created,
            "updated": self.updated,
        }

    def _recompute(self) -> str:
        return content_hash(self._core())

    def verify_integrity(self) -> bool:
        return bool(self.content_sha256) and self._recompute() == self.content_sha256

    def require_integrity(self) -> None:
        if not self.verify_integrity():
            raise KnowledgeIntegrityError(
                "decision record integrity check failed",
                decision_id=self.decision_id,
                expected=self.content_sha256,
                actual=self._recompute(),
            )

    def transition_to(self, target: Lifecycle, *, updated: str | None = None) -> DecisionRecord:
        if not self.lifecycle.can_transition_to(target):
            raise LifecycleTransitionError(
                "illegal decision lifecycle transition",
                at=self.decision_id,
                current=self.lifecycle.value,
                target=target.value,
            )
        from dataclasses import replace

        moved = replace(
            self,
            lifecycle=target,
            updated=updated if updated is not None else self.updated,
            content_sha256="",
        )
        return moved.sealed()

    @property
    def is_reviewable(self) -> bool:
        """True iff the decision carries the minimum record to be reviewed (Part 11)."""
        return bool(
            self.problem_statement
            and self.objective
            and self.alternatives
            and self.chosen_architecture
            and self.rationale
        )

    def to_dict(self) -> dict[str, Any]:
        payload = self._core()
        payload["content_sha256"] = self.content_sha256
        return payload


__all__ = [
    "RejectedOption",
    "CanonicalKnowledgeObject",
    "DecisionRecord",
]
