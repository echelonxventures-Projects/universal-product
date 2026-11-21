"""EC3-B10-U08 — The Universal Quality construct (DMC-09).

Realizes the meta-model construct **DMC-09 Quality-Object** (DATA-005 §2; DATA-013 §3):

    the **decidable, evaluative measurement of a data construct's fidelity** — its
    accuracy, completeness, consistency, and integrity — recorded as a measure against
    the construct (the ontology root DOE-09), classified by DXH-09 (Accuracy /
    Completeness / Consistency / Integrity measure). A quality object is an ENG-002
    Object classified by an ENG-004 Type, recorded against a data construct via
    ``measures`` (DMR-08) and binding measurement evaluation *by reference* to the frozen
    RUNTIME policy concern (DMR-11). Data quality is neither the data it measures nor an
    enforcement mechanism — it is an **evaluative measurement record that enacts
    nothing**.

The construct is **additive over the CERTIFIED EC-1 foundation *and* the CERTIFIED
DMC-02 Entity**, reusing both *by reference* (UDL-02 / DMI-05):

* Identity is derived through the EC-1 certified deterministic encoding
  (:func:`engine.certification.contracts.canonical_json` /
  :func:`~engine.certification.contracts.content_hash`) — no second identity scheme.
* The measured subject (DMR-08 ``measures``) is a **reference to a CERTIFIED data
  construct** (id + structural digest + name/type + meta-class), **never owned,
  embedded, or copied** (DQA-C3 by record; DMX-02 non-absorbing).
* Measurement evaluation is a **RUNTIME policy reference** only (``behaves-as``,
  DMR-11 / DQA-06) — no profiling engine, cleansing pipeline, or scheduler is defined.
* Completeness/consistency measurement is **schema-relative** (DQA-05 / DQA-C2): the
  declared schema (DMC-05) is bound *by reference*, never realized here.

**No profiling engine, data-quality/cleansing tool, benchmark technology, or vendor is
selected** (UDL-14 / DQA-07 / DQA-K5) — enforced fail-closed by a technology-marker scan
over the whole construct. A quality object **remediates nothing and confers no
authority** (DQA-03 / DQA-09 / DQA-K5): this is the material exercise of UDL-14 Quality
as an Evaluative Facet — quality *is* a measurement record that enacts nothing.

A :class:`QualityObject` is *immutable* (frozen — ENG-002 objecthood), *typed*
(ENG-004, DQA-K1/UDL-03), *identified* (ENG-001, DQA-K1/UDL-04), *subject-bound*
(``measures`` a CERTIFIED construct by reference — DMR-08), *dimensioned and evaluative*
(DQA-01/02/K2), *recorded* (DQA-04/K4), *versioned*, and holds a *forward-only lifecycle
state* (DOS-01…05, UDL-12). Constructing a :class:`QualityObject` enforces
DQA-K1/K2/K3/K4/K5, the measurement rules DQA-C1/C2/C3/C4, and UDL-14/03/04/05
**fail-closed**: an ill-formed, remediating, or authority-conferring quality object
cannot exist.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

# --- DMC-02 reuse by reference (UDL-02) — never redefined -------------------------
from data.entity import Entity
from data.quality_meta import (
    DIMENSION_FOR_KIND,
    LIFECYCLE_ORDER,
    QUALITY_DIMENSIONS,
    QUALITY_META_CLASS,
    QUALITY_RELATIONSHIPS,
    QUALITY_SUBSTRATE_REFS,
    SCHEMA_RELATIVE_KINDS,
    SCORE_MAX,
    SCORE_MIN,
    QualityKind,
    QualityState,
    QualityVerdict,
)

# --- EC-1 reuse by reference (UDL-02 / DMI-05) — imported, never redefined --------
from engine.certification.contracts import canonical_json, content_hash

#: The deterministic id prefix for a realized Quality object (mirrors EC-1 UCOS-<K>-<hex>).
QUALITY_ID_PREFIX = "UCOS-QUALITY"

#: The reference prefix a quality object presents to bind RUNTIME policy evaluation
#: (DMR-11 / DQA-06 / DOB-06 evaluate) — declarative, non-enforcing.
POLICY_REF_PREFIX = "UCOS-POLICY-REF"

#: The reference prefix a schema-relative measure cites for its declared schema
#: (DQA-05 / DQA-C2) — the DMC-05 schema is bound by reference, never realized here.
SCHEMA_REF_PREFIX = "UCOS-SCHEMA-REF"

#: The prefix of a CERTIFIED data-construct identity (the DMR-08 ``measures`` target).
CERTIFIED_ID_PREFIX = "UCOS-"

#: The map of EC-1 / DMC-02 primitives this construct reuses *by reference* (never
#: redefined). Recorded for the reuse-integrity check (UDL-02 / DMI-05 / VC-5).
REUSE_REFS: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the measurement record)",
    "ENG-004": "data.quality_meta.QualityKind + type_tag (ENG-004 typing discipline)",
    "ENG-005": "measured-construct + RUNTIME policy identity references (DMR-08/11)",
    "DMC-02": "data.entity.Entity — a CERTIFIED measures target (DMR-08); referenced only",
    "RL-F2": "RUNTIME policy — measurement evaluation bound by reference (DMR-11 / DQA-06)",
}

#: Conservative secret markers used to enforce UDL-15 / DQA-09 / RR-07 (embed no secret).
_SECRET_MARKERS: tuple[str, ...] = (
    "password",
    "secret",
    "private_key",
    "privatekey",
    "api_key",
    "apikey",
    "access_token",
    "credential",
    "-----begin",
)

#: Conservative quality-technology markers used to enforce **UDL-14 / DQA-07 / DQA-K5**
#: (select no profiling engine, data-quality/cleansing tool, benchmark technology, or
#: vendor). A quality object naming any of these is rejected fail-closed — quality is a
#: decidable, evaluative, non-remediating measurement record only. This is the material
#: exercise of UDL-14 (Quality as an Evaluative Facet) and DQA-07 (Benchmark Neutrality).
_TECH_MARKERS: tuple[str, ...] = (
    "great expectations",
    "deequ",
    "pandas profiling",
    "ydata-profiling",
    "soda core",
    "soda sql",
    "monte carlo",
    "talend",
    "informatica",
    "ataccama",
    "collibra",
    "anomalo",
    "bigeye",
    "profiling engine",
    "data quality tool",
    "cleansing engine",
    "cleansing pipeline",
    "remediation engine",
    "quality benchmark",
    "benchmark metric",
    "scheduler engine",
)


def policy_ref_for(predicate: str) -> str:
    """The reference a quality object presents to bind RUNTIME policy (DMR-11 / DQA-06).

    A quality object's measurement evaluation is a *reference* to the frozen RL-F2 policy
    concern (DOB-06 evaluate), which is declarative and non-enforcing by construction —
    never a redefined profiling engine.
    """
    return f"{POLICY_REF_PREFIX}:{predicate}"


class QualityError(ValueError):
    """Raised when a value cannot be realized as a well-formed :class:`QualityObject`.

    A :class:`QualityObject` is fail-closed (TRACK-001): an ill-formed, remediating,
    authority-conferring, or technology-bound quality record is rejected at construction
    rather than admitted as an invalid or constitutive object.
    """


@dataclass(frozen=True, slots=True)
class MeasuredConstructRef:
    """A reference to a CERTIFIED data construct a quality object ``measures`` (DMR-08).

    Records **only** the measured construct's identity, structural fingerprint, name,
    type, and meta-class — never its implementation — so the quality object references,
    and never owns or absorbs, the construct it measures (DMX-02 non-absorbing; DQA-C3 by
    record; UDL-02 reuse-by-reference).
    """

    construct_id: str
    structure_digest: str
    name: str
    type_tag: str
    meta_class: str

    @classmethod
    def from_entity(cls, entity: Entity) -> MeasuredConstructRef:
        """Project a CERTIFIED :class:`~data.entity.Entity` into a measured-construct ref."""
        if not isinstance(entity, Entity):
            raise QualityError("a quality object measures a data construct (DMR-08)")
        return cls(
            construct_id=entity.entity_id,
            structure_digest=entity.structure_digest,
            name=entity.name,
            type_tag=entity.type_tag,
            meta_class=entity.meta_class,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "construct_id": self.construct_id,
            "structure_digest": self.structure_digest,
            "name": self.name,
            "type_tag": self.type_tag,
            "meta_class": self.meta_class,
            "binding": "DMR-08:measures",
            "owned": False,  # DQA-C3 — measured by record, never owned
            "absorbing": False,  # DMX-02 — referenced, not absorbed
        }


@dataclass(frozen=True, slots=True)
class MeasurementEntry:
    """A single recorded, decidable quality measurement along one dimension (DQA-C1).

    Purely evaluative: it *records* a decidable verdict and a bounded metric value for
    the measured dimension; it remediates nothing and mutates nothing (DQA-03 / DQA-C3).
    """

    dimension: str
    satisfied: bool
    score: int = SCORE_MAX
    note: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.dimension, str) or self.dimension not in QUALITY_DIMENSIONS:
            raise QualityError(
                "a measurement names a decidable quality dimension "
                "(accuracy/completeness/consistency/integrity) — DQA-02"
            )
        if not isinstance(self.satisfied, bool):
            raise QualityError("a measurement records a decidable verdict (DQA-C1)")
        if isinstance(self.score, bool) or not isinstance(self.score, int):
            raise QualityError("a measurement records an integer metric value (DQA-C3)")
        if not (SCORE_MIN <= self.score <= SCORE_MAX):
            raise QualityError(
                f"a measurement score is a bounded metric in [{SCORE_MIN}, {SCORE_MAX}] (DQA-C3)"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension,
            "satisfied": self.satisfied,
            "score": self.score,
            "note": self.note,
        }


@dataclass(frozen=True, slots=True)
class QualityObject:
    """DMC-09 — an immutable, evaluative, non-remediating, non-authoritative quality record.

    Fields:
        name:         the explicit quality-object name (part of identity).
        type_tag:     the ENG-004 Type of the object (DQA-K1; UDL-03).
        kind:         the DXH-09 classification (Accuracy / Completeness / Consistency /
                      Integrity measure; DMR-09 classified-by).
        measured_ref: the CERTIFIED construct the object ``measures`` (DMR-08; DQA-C3
                      by record, non-owning).
        policy_ref:   the RUNTIME policy reference measurement binds to (DMR-11 / DQA-06 /
                      DQA-K3). A reference obligation only — no profiling engine is defined.
        measurements: the recorded per-dimension measurements (DQA-C1). Required
                      non-empty; every measurement is along the kind's single facet
                      (DXC-02 / DQA-02).
        verdict:      the recorded quality judgment (DQA-C1 / DOV-08).
        schema_ref:   the declared-schema reference for a schema-relative measure
                      (DQA-05 / DQA-C2). Required for completeness/consistency measures;
                      empty otherwise.
        state:        the DOS-01…05 forward-only lifecycle state (UDL-12).
        version:      the object version (append-only re-measurement; DQA-C5 / UDL-12/15).
        supersedes:   the id of a superseded quality object (DQA-C5 append-only).
    """

    name: str
    type_tag: str
    kind: QualityKind
    measured_ref: MeasuredConstructRef
    policy_ref: str
    measurements: tuple[MeasurementEntry, ...] = ()
    verdict: QualityVerdict = QualityVerdict.PASS
    schema_ref: str = ""
    state: QualityState = QualityState.DEFINED
    version: str = "1.0.0"
    supersedes: str = ""

    def __post_init__(self) -> None:
        # explicit, decidable name.
        if not isinstance(self.name, str) or not self.name.strip():
            raise QualityError("quality object must have an explicit name")
        # DQA-K1 / DMK-01 / UDL-03 — typed (ENG-004): a decidable, non-empty type.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise QualityError("quality object must be typed with an ENG-004 type_tag (DQA-K1)")
        # DXH-09 / DMR-09 — classified by exactly one quality kind.
        if not isinstance(self.kind, QualityKind):
            raise QualityError("quality kind must be a DXH-09 QualityKind (DMR-09)")
        # DMR-08 — the measured subject is a reference to a CERTIFIED construct.
        if not isinstance(self.measured_ref, MeasuredConstructRef):
            raise QualityError("quality measures a CERTIFIED construct by reference (DMR-08)")
        if not self.measured_ref.construct_id.startswith(CERTIFIED_ID_PREFIX):
            raise QualityError("the measured subject is not a CERTIFIED construct id (DMR-08)")
        if len(self.measured_ref.structure_digest) != 64 or any(
            c not in "0123456789abcdef" for c in self.measured_ref.structure_digest
        ):
            raise QualityError("the measured subject carries no structural digest (UDL-06)")
        # DMR-11 / DQA-06 / DQA-K3 — measurement binds a RUNTIME policy reference.
        if not isinstance(self.policy_ref, str) or not self.policy_ref.startswith(
            f"{POLICY_REF_PREFIX}:"
        ):
            raise QualityError(
                "measurement must bind a RUNTIME policy reference (DMR-11 / DQA-K3)"
            )
        # DQA-C1 / DQA-02 — records ≥1 decidable measurement along the kind's single facet.
        if not isinstance(self.measurements, tuple):
            raise QualityError("measurements must be a tuple of MeasurementEntry (DQA-C1)")
        if not self.measurements:
            raise QualityError("a quality object records ≥1 measurement (DQA-C1)")
        facet = DIMENSION_FOR_KIND[self.kind]
        for entry in self.measurements:
            if not isinstance(entry, MeasurementEntry):
                raise QualityError("measurements are MeasurementEntry records (DQA-C1)")
            if entry.dimension != facet:
                raise QualityError(
                    f"a {self.kind.value} measures only the '{facet}' dimension "
                    f"(single-facet, DXC-02 / DQA-02)"
                )
        # DQA-C1 / DOV-08 — records a decidable verdict.
        if not isinstance(self.verdict, QualityVerdict):
            raise QualityError("verdict must be a decidable QualityVerdict (DQA-C1)")
        # DQA-05 / DQA-C2 — completeness/consistency are schema-relative (schema by ref).
        if not isinstance(self.schema_ref, str):
            raise QualityError("schema_ref must be a string (DQA-05)")
        if self.kind in SCHEMA_RELATIVE_KINDS:
            if not self.schema_ref.startswith(f"{SCHEMA_REF_PREFIX}:"):
                raise QualityError(
                    "a completeness/consistency measure is schema-relative — it must bind a "
                    "declared-schema reference (DQA-05 / DQA-C2)"
                )
        elif self.schema_ref and not self.schema_ref.startswith(f"{SCHEMA_REF_PREFIX}:"):
            raise QualityError("schema_ref, when present, is a declared-schema reference (DQA-05)")
        # V5 / UDL-12 — a valid forward-only lifecycle state.
        if not isinstance(self.state, QualityState):
            raise QualityError("quality state must be a DOS-01…05 state (UDL-12)")
        # DQA-08 — a quality object records an explicit, non-empty version.
        if not isinstance(self.version, str) or not self.version.strip():
            raise QualityError("quality object must record an explicit version (DQA-08)")
        if not isinstance(self.supersedes, str):
            raise QualityError("quality supersedes reference must be a string (DQA-C5)")
        # UDL-14 / DQA-07 / DQA-K5 — names no profiling/benchmark technology (material).
        if self._scan_technology():
            raise QualityError(
                "quality names a profiling/data-quality/benchmark technology or vendor "
                "(UDL-14 / DQA-07 / DQA-K5)"
            )

    # -- technology-neutrality (UDL-14, material) ------------------------------

    def _scan_technology(self) -> bool:
        """True iff any technology marker appears in the object's declared surface."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECH_MARKERS)

    def names_technology(self) -> bool:
        """UDL-14 / DQA-07 / DQA-K5 / C6 — True iff the object names a quality tech."""
        return self._scan_technology()

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the object (structure + measured reference)."""
        return {
            "meta_class": QUALITY_META_CLASS,
            "name": self.name,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "measured_ref": {
                "construct_id": self.measured_ref.construct_id,
                "structure_digest": self.measured_ref.structure_digest,
                "name": self.measured_ref.name,
                "type_tag": self.measured_ref.type_tag,
                "meta_class": self.measured_ref.meta_class,
            },
            "policy_ref": self.policy_ref,
            "measurements": [
                {
                    "dimension": m.dimension,
                    "satisfied": m.satisfied,
                    "score": m.score,
                    "note": m.note,
                }
                for m in self.measurements
            ],
            "verdict": self.verdict.value,
            "schema_ref": self.schema_ref,
            "version": self.version,
            "supersedes": self.supersedes,
        }

    @property
    def structure_digest(self) -> str:
        """The EC-1 content hash of the object core — its structural fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def quality_id(self) -> str:
        """The deterministic ENG-001 identity of the object (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (UDL-04 — no second identity
        scheme): an identical object always yields the identical id, so identity is
        reproducible and byte-stable (determinism, VC-4).
        """
        return f"{QUALITY_ID_PREFIX}-{self.name}-{self.structure_digest[:16]}"

    # -- meta-model participation (DATA-005 / DATA-013) ------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (DMC-09)."""
        return QUALITY_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the DMR-01…12 relationships the object participates in."""
        return QUALITY_RELATIONSHIPS

    def measured_construct_id(self) -> str:
        """The identity of the construct this object measures (DMR-08; by reference)."""
        return self.measured_ref.construct_id

    def measured_dimension(self) -> str:
        """The single quality dimension this object measures (DXC-02 / DQA-02)."""
        return DIMENSION_FOR_KIND[self.kind]

    def measured_dimensions(self) -> tuple[str, ...]:
        """The distinct dimensions recorded across the measurements (DQA-02)."""
        return tuple(dict.fromkeys(m.dimension for m in self.measurements))

    # -- quality property predicates -------------------------------------------

    def is_evaluative(self) -> bool:
        """DQA-01 / DQA-K2 — quality is a decidable, evaluative measurement."""
        return True

    def is_dimensioned(self) -> bool:
        """DQA-02 — the object measures a decidable quality dimension."""
        return all(m.dimension in QUALITY_DIMENSIONS for m in self.measurements)

    def remediates(self) -> bool:
        """DQA-03 / DQA-K2 — quality measures and records; it remediates nothing."""
        return False

    def enforces(self) -> bool:
        """DQA-03 / UDL-14 — quality enacts no enforcement (structurally none)."""
        return False

    def grants_access(self) -> bool:
        """DQA-09 / DQA-K5 — quality grants no access (structurally none)."""
        return False

    def is_recorded(self) -> bool:
        """DQA-04 / DQA-K4 — the measurement is recorded against an ENG-002 object (DOV-08)."""
        return True

    def binds_policy_by_reference(self) -> bool:
        """DMR-11 / DQA-06 / DQA-K3 — measurement binds a RUNTIME policy reference only."""
        return self.policy_ref.startswith(f"{POLICY_REF_PREFIX}:")

    def records_measurement(self) -> bool:
        """DQA-C1 — the object decidably records ≥1 per-dimension measurement."""
        return bool(self.measurements)

    def is_schema_relative(self) -> bool:
        """DQA-05 / DQA-C2 — a completeness/consistency measure binds a schema by reference."""
        if self.kind in SCHEMA_RELATIVE_KINDS:
            return self.schema_ref.startswith(f"{SCHEMA_REF_PREFIX}:")
        return True

    def gap_report(self) -> tuple[str, ...]:
        """DQA-C4 — the dimensions recorded as deficient, routed to a Gap Report (record-only).

        Quality *records* deficiencies and routes them to a Gap Report; it does not itself
        remediate or enforce (DQA-03 / DQA-C4).
        """
        return tuple(m.dimension for m in self.measurements if not m.satisfied)

    def passes(self) -> bool:
        """Whether the recorded measurements show no deficiency (evaluative only)."""
        return not self.gap_report()

    def is_classified(self) -> bool:
        """DXH-09 — the object is classified by exactly one quality kind."""
        return isinstance(self.kind, QualityKind)

    def is_founding_acyclic(self) -> bool:
        """V4 / DMK-03 — the founding/measurement graph is acyclic.

        The object's founding references (``measures`` → construct, ``behaves-as`` →
        RUNTIME policy, schema reference) are recorded by *identity reference*; none may
        reference the object itself, so the founding graph is a DAG.
        """
        own = self.quality_id
        refs = {self.measured_construct_id(), self.policy_ref, self.schema_ref}
        return own not in refs

    def measures_construct(self, construct_id: str) -> bool:
        """DMR-08 — whether this object measures the construct ``construct_id``."""
        return construct_id == self.measured_construct_id()

    def absorbs_measured(self) -> bool:
        """DQA-C3 / DMX-02 — the object references the construct it measures, never owns it."""
        return False

    # -- non-constitutiveness (UDL-14/15 / DQA-07/09) --------------------------

    def confers_authority(self) -> bool:
        """UDL-14/15 / DQA-09 / C7 — a quality object confers no authority (material)."""
        return False

    def embeds_secret(self) -> bool:
        """UDL-15 / DQA-09 / RR-07 / C7 — True iff the object appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_el1(self) -> bool:
        """UDL-02 / DMI-05 / VC-5 — a quality object redefines no EL-1/DMC-02/RL-F2 model."""
        return False

    def selects_technology(self) -> bool:
        """UDL-14 / DQA-07 / DQA-K5 — a quality object selects no benchmark tech (material)."""
        return self._scan_technology()

    # -- lifecycle (UDL-12, forward-only) --------------------------------------

    def transition(self, to_state: QualityState) -> QualityObject:
        """Return a new object advanced to ``to_state`` (forward-only; UDL-12).

        A re-measurement is a new record, never in-place mutation (DATA-013 §8; UDL-12/15;
        DQA-C5 append-only).

        Raises:
            QualityError: on a backward transition.
        """
        if not isinstance(to_state, QualityState):
            raise QualityError("target state must be a DOS-01…05 state (UDL-12)")
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise QualityError(
                f"lifecycle is forward-only (UDL-12): "
                f"{self.state.value} → {to_state.value} is backward"
            )
        return replace(self, state=to_state)

    # -- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the quality object."""
        return {
            "quality_id": self.quality_id,
            "meta_class": self.meta_class,
            "name": self.name,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "measured_ref": self.measured_ref.to_dict(),
            "measured_construct_id": self.measured_construct_id(),
            "measured_dimension": self.measured_dimension(),
            "measured_dimensions": list(self.measured_dimensions()),
            "policy_ref": self.policy_ref,
            "binds_policy_by_reference": self.binds_policy_by_reference(),
            "measurements": [m.to_dict() for m in self.measurements],
            "records_measurement": self.records_measurement(),
            "verdict": self.verdict.value,
            "gap_report": list(self.gap_report()),
            "passes": self.passes(),
            "schema_ref": self.schema_ref,
            "schema_relative": self.is_schema_relative(),
            "evaluative": self.is_evaluative(),
            "dimensioned": self.is_dimensioned(),
            "remediates": self.remediates(),
            "enforces": self.enforces(),
            "grants_access": self.grants_access(),
            "recorded": self.is_recorded(),
            "confers_authority": self.confers_authority(),
            "names_technology": self.names_technology(),
            "classified": self.is_classified(),
            "version": self.version,
            "supersedes": self.supersedes,
            "state": self.state.value,
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(QUALITY_SUBSTRATE_REFS),
            "absorbs_measured": self.absorbs_measured(),
        }


def make_measurements(
    entries: tuple[tuple[str, bool, int], ...],
) -> tuple[MeasurementEntry, ...]:
    """Build a tuple of :class:`MeasurementEntry` from ``(dimension, satisfied, score)`` triples."""
    return tuple(
        MeasurementEntry(dimension=dim, satisfied=ok, score=score) for dim, ok, score in entries
    )


def make_quality(
    name: str,
    type_tag: str,
    measured: Entity | MeasuredConstructRef,
    policy_ref: str,
    *,
    kind: QualityKind = QualityKind.COMPLETENESS_MEASURE,
    measurements: tuple[MeasurementEntry, ...] = (),
    verdict: QualityVerdict = QualityVerdict.PASS,
    schema_ref: str = "",
    state: QualityState = QualityState.DEFINED,
    version: str = "1.0.0",
    supersedes: str = "",
) -> QualityObject:
    """Construct a well-formed :class:`QualityObject` (fail-closed factory).

    ``measured`` is the construct the object measures — either a CERTIFIED
    :class:`~data.entity.Entity` (reused by reference — the DMR-08 ``measures`` target) or
    an already-projected :class:`MeasuredConstructRef`.
    """
    measured_ref = (
        measured
        if isinstance(measured, MeasuredConstructRef)
        else MeasuredConstructRef.from_entity(measured)
    )
    return QualityObject(
        name=name,
        type_tag=type_tag,
        kind=kind,
        measured_ref=measured_ref,
        policy_ref=policy_ref,
        measurements=tuple(measurements),
        verdict=verdict,
        schema_ref=schema_ref,
        state=state,
        version=version,
        supersedes=supersedes,
    )


__all__ = [
    "QUALITY_ID_PREFIX",
    "POLICY_REF_PREFIX",
    "SCHEMA_REF_PREFIX",
    "CERTIFIED_ID_PREFIX",
    "REUSE_REFS",
    "policy_ref_for",
    "QualityError",
    "MeasuredConstructRef",
    "MeasurementEntry",
    "QualityObject",
    "make_measurements",
    "make_quality",
]
