"""EC2-CAP-SEC-001 / SEC-CLASS — Security Classification model & ledger (Phase 1).

The heart of the **Security Classification Runtime**: the immutable, evaluative,
**non-enforcing** :class:`SecurityClassification` record and the append-only
:class:`ClassificationLedger` that records classifications and their bindings to
platform constructs.

A :class:`SecurityClassification` is the platform realization of the subject-layer
security records (DATA-014 / SERVICE-014 / APPLICATION-013 / INFRASTRUCTURE-013). It
is a **decidable predicate result recorded against a construct** — it *classifies*
and *records*; it grants no access, issues no credential, encrypts nothing, and
enacts no policy (ARCH-SECURITY-001 §4–§11; DATA-014 DZA-01; SERVICE-014 SSE-03;
APPLICATION-013 SEC-03/04; INFRASTRUCTURE-013 ISEC-01). Where a construct declares an
enforcement obligation, the classification carries an :class:`EnforcementReference`
that points at the existing certified L7 seam **by reference only** — SEC-CLASS never
authorizes (RG-02 / AR-04).

The :class:`ClassificationLedger` is SEC-CLASS's own append-only record surface (its
constitutional "Record" responsibility). It is **not** the seven-registry system of
SEC-REG (a later phase); it stores only security classifications. Every entry is
content-addressed and deterministic; there is no wall-clock in any identity or
fingerprint (IMP-007 §5).
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.security.contracts import (
    L7_BOUND_KINDS,
    SUBJECT_LAYER_KINDS,
    SUBJECT_LAYER_SOURCE,
    ClassificationKind,
    EnforcementReference,
    SubjectLayer,
)
from platform.security.errors import (
    ClassificationValidationError,
    SecurityClassificationError,
)
from typing import Any


@dataclass(frozen=True, slots=True)
class SecurityClassification:
    """An immutable, evaluative, non-enforcing security classification record.

    Records that a platform construct (``subject_ref``) bears a classification of a
    given ``kind`` (originating in a subject ``layer``) with an evaluative ``label``.
    For L7-bound kinds (Authentication / Authorization) it carries an
    :class:`EnforcementReference` to the certified decision point; for all other kinds
    ``enforcement_ref`` is ``None``. ``non_enforcing`` is invariantly ``True`` — the
    record enacts nothing. ``classification_id`` is content-addressed (deterministic).
    """

    kind: ClassificationKind
    layer: SubjectLayer
    subject_ref: str
    label: str
    constitution_ref: str
    enforcement_ref: EnforcementReference | None = None
    non_enforcing: bool = True
    classification_id: str = ""

    @classmethod
    def create(
        cls,
        kind: ClassificationKind,
        layer: SubjectLayer,
        subject_ref: str,
        label: str,
        *,
        enforcement_ref: EnforcementReference | None = None,
        constitution_ref: str | None = None,
    ) -> SecurityClassification:
        """Build a classification with a deterministic id, fail-closed on any violation."""
        if not isinstance(kind, ClassificationKind):
            raise SecurityClassificationError("classification kind must be a ClassificationKind")
        if not isinstance(layer, SubjectLayer):
            raise SecurityClassificationError(
                "classification layer must be a SubjectLayer", kind=kind.value
            )
        if not isinstance(subject_ref, str) or not subject_ref.strip():
            raise SecurityClassificationError(
                "classification requires a non-empty subject_ref (the classified construct)",
                kind=kind.value,
            )
        if not isinstance(label, str) or not label.strip():
            raise SecurityClassificationError(
                "classification requires a non-empty evaluative label",
                kind=kind.value,
                subject_ref=subject_ref,
            )
        # Decidable membership: the layer must be permitted to originate this kind.
        if kind not in SUBJECT_LAYER_KINDS[layer]:
            raise SecurityClassificationError(
                "subject layer does not originate this classification kind",
                kind=kind.value,
                layer=layer.value,
            )
        # Enforcement-reference consistency (record-only; never enacts).
        if kind in L7_BOUND_KINDS:
            if not isinstance(enforcement_ref, EnforcementReference):
                raise SecurityClassificationError(
                    "an L7-bound classification kind must carry an EnforcementReference",
                    kind=kind.value,
                    subject_ref=subject_ref,
                )
        elif enforcement_ref is not None:
            raise SecurityClassificationError(
                "a non-L7-bound classification kind must not carry an EnforcementReference",
                kind=kind.value,
                subject_ref=subject_ref,
            )
        source = constitution_ref if constitution_ref is not None else SUBJECT_LAYER_SOURCE[layer]
        if not isinstance(source, str) or not source.strip():
            raise SecurityClassificationError(
                "classification requires a constitution_ref for backward traceability",
                kind=kind.value,
            )
        core = {
            "kind": kind.value,
            "layer": layer.value,
            "subject_ref": subject_ref,
            "label": label,
            "constitution_ref": source,
            "enforcement_ref": enforcement_ref.to_dict() if enforcement_ref else None,
            "non_enforcing": True,
        }
        return cls(
            kind=kind,
            layer=layer,
            subject_ref=subject_ref,
            label=label,
            constitution_ref=source,
            enforcement_ref=enforcement_ref,
            non_enforcing=True,
            classification_id=f"UCOS-SCLS-{content_hash(core)[:16]}",
        )

    @property
    def is_l7_bound(self) -> bool:
        """True iff this classification's enforcement obligation resolves to the L7 seam."""
        return self.kind in L7_BOUND_KINDS

    def classify(self) -> dict[str, Any]:
        """Return the evaluative, decidable verdict for this record (enacts nothing).

        This is a pure evaluation: it reports the recorded classification decision;
        it grants no access and enforces nothing (``enforced`` is always ``False``).
        """
        return {
            "classification_id": self.classification_id,
            "kind": self.kind.value,
            "subject_ref": self.subject_ref,
            "label": self.label,
            "decidable": True,
            "enforced": False,
            "non_enforcing": True,
        }

    def trace(self) -> dict[str, Any]:
        """Return the full traceability chain (ARCH-SECURITY-001 §14).

        Backward: constitutional source + originating subject layer. Subject: the
        classified construct. Forward: the L7 enforcement reference (or ``None``).
        """
        return {
            "classification_id": self.classification_id,
            "backward": {
                "layer": self.layer.value,
                "constitution_ref": self.constitution_ref,
            },
            "subject": {"subject_ref": self.subject_ref, "kind": self.kind.value},
            "forward": (
                self.enforcement_ref.to_dict() if self.enforcement_ref is not None else None
            ),
        }

    def validate(self) -> dict[str, Any]:
        """Re-affirm meta-validity (typed · identified · non-enforcing · reference-consistent).

        Returns a structured, decidable validation record. Raises
        :class:`ClassificationValidationError` only if an invariant is violated (which
        :meth:`create` already prevents, so this is a defensive re-check for callers).
        """
        checks = {
            "typed": isinstance(self.kind, ClassificationKind)
            and isinstance(self.layer, SubjectLayer),
            "identified": self.classification_id.startswith("UCOS-SCLS-"),
            "non_enforcing": self.non_enforcing is True,
            "layer_originates_kind": self.kind in SUBJECT_LAYER_KINDS[self.layer],
            "enforcement_reference_consistent": (
                (self.kind in L7_BOUND_KINDS) == (self.enforcement_ref is not None)
            ),
        }
        if not all(checks.values()):
            failed = sorted(name for name, ok in checks.items() if not ok)
            raise ClassificationValidationError(
                "classification failed meta-validity",
                classification_id=self.classification_id,
                failed=",".join(failed),
            )
        return {
            "classification_id": self.classification_id,
            "meta_valid": True,
            "checks": checks,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "classification_id": self.classification_id,
            "kind": self.kind.value,
            "layer": self.layer.value,
            "subject_ref": self.subject_ref,
            "label": self.label,
            "constitution_ref": self.constitution_ref,
            "enforcement_ref": (
                self.enforcement_ref.to_dict() if self.enforcement_ref is not None else None
            ),
            "non_enforcing": self.non_enforcing,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class ClassificationLedger:
    """SEC-CLASS's own deterministic, append-only classification record surface.

    Records :class:`SecurityClassification` entries and their bindings to constructs.
    Append-only and idempotent by ``classification_id`` (re-recording an identical
    classification returns the existing entry; it never mutates or duplicates). It is
    **not** the seven-registry SEC-REG system — it stores only security
    classifications for the classification runtime's "Record" and "Trace"
    responsibilities. It exposes **no** ratify/enact/override operation (RG-02/AR-04).
    """

    __slots__ = ("_entries", "_index")

    def __init__(self) -> None:
        self._entries: list[SecurityClassification] = []
        self._index: dict[str, int] = {}

    def record(self, classification: SecurityClassification) -> SecurityClassification:
        """Append a classification (idempotent by id); returns the stored entry."""
        if not isinstance(classification, SecurityClassification):
            raise SecurityClassificationError("only a SecurityClassification may be recorded")
        # Defensive meta-validity gate before recording (fail-closed).
        classification.validate()
        existing = self._index.get(classification.classification_id)
        if existing is not None:
            return self._entries[existing]
        self._index[classification.classification_id] = len(self._entries)
        self._entries.append(classification)
        return classification

    @property
    def classifications(self) -> tuple[SecurityClassification, ...]:
        """An immutable snapshot of the append-only ledger (in record order)."""
        return tuple(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, classification_id: str) -> bool:
        return classification_id in self._index

    def get(self, classification_id: str) -> SecurityClassification:
        """Return a recorded classification by id (raises if absent)."""
        idx = self._index.get(classification_id)
        if idx is None:
            raise SecurityClassificationError(
                "no such classification", classification_id=classification_id
            )
        return self._entries[idx]

    def by_kind(self, kind: ClassificationKind) -> tuple[SecurityClassification, ...]:
        """Every recorded classification of ``kind`` in record order (queryable)."""
        return tuple(c for c in self._entries if c.kind is kind)

    def by_layer(self, layer: SubjectLayer) -> tuple[SecurityClassification, ...]:
        """Every recorded classification originating in ``layer`` in record order."""
        return tuple(c for c in self._entries if c.layer is layer)

    def by_subject(self, subject_ref: str) -> tuple[SecurityClassification, ...]:
        """Every recorded classification bound to ``subject_ref`` in record order."""
        return tuple(c for c in self._entries if c.subject_ref == subject_ref)

    def fingerprint(self) -> str:
        """A deterministic fingerprint over the ordered ledger."""
        return content_hash([c.to_dict() for c in self._entries])

    def to_dict(self) -> dict[str, Any]:
        return {
            "classification_count": len(self._entries),
            "classifications": [c.to_dict() for c in self._entries],
        }


__all__ = ["SecurityClassification", "ClassificationLedger"]
